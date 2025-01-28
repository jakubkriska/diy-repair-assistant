# DIY repair assistent

## Description:
DIY assistent assisting with diagnosis of damaged objects providing tailored step-by-step reparation guides.

```yml

app:
  description: Assisting you in the process of reparations of various objects.
  icon: 🤖
  icon_background: '#FFEAD5'
  mode: advanced-chat
  name: DIY - reparation assistent
  use_icon_as_answer_icon: true
  kind: app
  version: 0.1.5
workflow:
  conversation_variables: []
  environment_variables: []
  features:
    file_upload:
      allowed_file_extensions:
      - .JPG
      - .JPEG
      - .PNG
      - .GIF
      - .WEBP
      - .SVG
      allowed_file_types:
      - image
      allowed_file_upload_methods:
      - local_file
      - remote_url
      enabled: false
      fileUploadConfig:
        audio_file_size_limit: 50
        batch_count_limit: 5
        file_size_limit: 15
        image_file_size_limit: 10
        video_file_size_limit: 100
        workflow_file_upload_limit: 10
      image:
        enabled: false
        number_limits: 3
        transfer_methods:
        - local_file
        - remote_url
      number_limits: 3
    opening_statement: ''
    retriever_resource:
      enabled: true
    sensitive_word_avoidance:
      enabled: false
    speech_to_text:
      enabled: false
    suggested_questions: []
    suggested_questions_after_answer:
      enabled: false
    text_to_speech:
      enabled: false
      language: ''
      voice: ''
  graph:
    edges:
    - data:
        sourceType: start
        targetType: llm
      id: 1736853735221-llm
      selected: false
      source: '1736853735221'
      sourceHandle: source
      target: llm
      targetHandle: target
      type: custom
    - data:
        isInIteration: false
        sourceType: llm
        targetType: answer
      id: llm-source-answer-target
      source: llm
      sourceHandle: source
      target: answer
      targetHandle: target
      type: custom
      zIndex: 0
    nodes:
    - data:
        desc: ''
        selected: false
        title: Start
        type: start
        variables: []
      height: 54
      id: '1736853735221'
      position:
        x: 80
        y: 282
      positionAbsolute:
        x: 80
        y: 282
      selected: false
      sourcePosition: right
      targetPosition: left
      type: custom
      width: 244
    - data:
        context:
          enabled: false
          variable_selector: []
        desc: ''
        memory:
          query_prompt_template: '{{#sys.query#}}'
          role_prefix:
            assistant: ''
            user: ''
          window:
            enabled: false
            size: 10
        model:
          completion_params:
            temperature: 0.7
          mode: chat
          name: llama-3.3-70b-specdec
          provider: groq
        prompt_template:
        - edition_type: jinja2
          id: f476b96c-1079-4984-ae0e-7ca4b665e378
          jinja2_text: "{\n  \"introduction\": {\n    \"prompt\": \"Hello! I'm your\
            \ DIY Repair Assistant. \U0001F6E0️\\n\\nI’m here to help you repair household\
            \ items with step-by-step guidance based on common repair techniques and\
            \ examples. Please note that my suggestions are general and may need some\
            \ adaptation to fit your specific situation. Also, I only assist with\
            \ **item repairs**—not medical, legal, or other non-repair-related topics.\\\
            n\\nLet’s get started! Tell me:\\n1️⃣ What item you’re repairing.\\n2️⃣\
            \ The specific issue you’re facing.\"\n  },\n  \"problem_identification\"\
            : {\n    \"prompt\": \"Got it! Let’s start by understanding the problem\
            \ better. Could you describe the issue in more detail? For example:\\\
            n- Is it broken, loose, leaking, or something else?\\n- Do you see any\
            \ visible damage, like cracks or fraying?\\n\\nIf possible, you can also\
            \ upload a photo of the item to help me guide you better.\",\n    \"input\"\
            : {\n      \"type\": \"text_or_image\",\n      \"next_step\": \"user_preferences\"\
            \n    }\n  },\n  \"user_preferences\": {\n    \"prompt\": \"To provide\
            \ the best solution, I’d like to know a bit about your priorities:\\n1️⃣\
            \ **Time:** How much time do you have for this repair? (e.g., under 1\
            \ hour, a few hours, or a whole day)\\n2️⃣ **Budget:** What’s your budget\
            \ for materials or tools? (e.g., low, medium, or high)\\n3️⃣ **Quality:**\
            \ Do you prioritize durability, appearance, or usability?\",\n    \"input\"\
            : {\n      \"type\": \"multiple_choice\",\n      \"choices\": {\n    \
            \    \"time\": [\"Under 1 hour\", \"A few hours\", \"A whole day\"],\n\
            \        \"budget\": [\"Low\", \"Medium\", \"High\"],\n        \"quality\"\
            : [\"Durability\", \"Appearance\", \"Usability\"]\n      },\n      \"\
            next_step\": \"solution_recommendation\"\n    }\n  },\n  \"solution_recommendation\"\
            : {\n    \"prompt\": \"Based on your answers, I’ve found a solution for\
            \ you:\\n✅ **Approach:** {approach}\\n✅ **Estimated Time:** {time}\\n✅\
            \ **Budget:** {budget}\\n\\nWould you like me to provide a detailed step-by-step\
            \ guide?\",\n    \"input\": {\n      \"type\": \"yes_no\",\n      \"next_step\"\
            : {\n        \"yes\": \"step_by_step_guide\",\n        \"no\": \"end\"\
            \n      }\n    }\n  },\n  \"step_by_step_guide\": {\n    \"prompt\": \"\
            Here’s your step-by-step guide for fixing the problem:\\n\\n1️⃣ {step_1}\\\
            n2️⃣ {step_2}\\n3️⃣ {step_3}\\n...\\n\\nWould you like additional visual\
            \ aids, like diagrams or videos, for these steps?\",\n    \"input\": {\n\
            \      \"type\": \"yes_no\",\n      \"next_step\": {\n        \"yes\"\
            : \"visual_support\",\n        \"no\": \"material_recommendations\"\n\
            \      }\n    }\n  },\n  \"visual_support\": {\n    \"prompt\": \"Here\
            \ are some visual aids to help you:\\n- Video Guide: {video_link}\\n-\
            \ Step Diagrams: {diagram_link}\\n\\nLet me know if you need further clarification!\"\
            ,\n    \"next_step\": \"material_recommendations\"\n  },\n  \"material_recommendations\"\
            : {\n    \"prompt\": \"To complete this repair, you’ll need:\\n- **{material_1}**:\
            \ [Buy here]({link_1})\\n- **{material_2}**: [Buy here]({link_2})\\n-\
            \ **{material_3}**: [Buy here]({link_3})\\n\\nWould you like me to find\
            \ materials in your local area or suggest alternatives?\",\n    \"input\"\
            : {\n      \"type\": \"multiple_choice\",\n      \"choices\": [\"Local\
            \ materials\", \"Alternatives\"],\n      \"next_step\": \"motivation_and_support\"\
            \n    }\n  },\n  \"motivation_and_support\": {\n    \"prompt\": \"You’re\
            \ doing great! Keep going—you’ll have this fixed in no time. \U0001F60A\
            \\n\\nIf you run into any trouble, feel free to ask me questions or upload\
            \ a picture of your progress.\",\n    \"next_step\": \"end\"\n  },\n \
            \ \"end\": {\n    \"prompt\": \"Thanks for using DIY Repair Assistant!\
            \ If you have more items to fix, just let me know. Happy repairing! \U0001F6E0\
            ️\"\n  }\n}"
          role: system
          text: '{ "introduction": { "prompt": "Hello! I''m your DIY Repair Assistant.
            🛠️\n\nI specialize in helping you repair objects and household items quickly,
            affordably, and effectively. My focus is strictly on repair-related tasks,
            so I won’t provide guidance on unrelated topics like medical, legal, or
            non-repair issues.\n\nTo get started, please share:\n1️⃣ The item you''re
            repairing (e.g., chair, phone, washing machine).\n2️⃣ The specific problem
            you''re facing (e.g., broken part, loose joint, or not functioning).\n\nLet’s
            fix it together!" }, "problem_identification": { "prompt": "Thanks for
            sharing! Let’s dig deeper:\n- Is the item physically damaged (e.g., cracked,
            torn, detached)?\n- Is it a functional issue (e.g., not turning on, leaking)?\n-
            Can you upload a photo to help me understand the problem better?\n\nThe
            more details, the better I can assist you." }, "solution_recommendation":
            { "prompt": "Based on your description, here’s a recommended approach:\n✅
            **Problem:** {problem_description}\n✅ **Solution:** {repair_method}\n✅
            **Estimated Time:** {estimated_time}\n✅ **Materials Needed:** {materials_list}\n\nWould
            you like step-by-step instructions for this repair?", "input": { "type":
            "yes_no", "next_step": { "yes": "step_by_step_guide", "no": "end" } }
            }, "step_by_step_guide": { "prompt": "Here’s your detailed step-by-step
            guide:\n\n1️⃣ {step_1}\n2️⃣ {step_2}\n3️⃣ {step_3}\n...\n\nNeed visuals
            (e.g., diagrams or videos) for these steps?", "input": { "type": "yes_no",
            "next_step": { "yes": "visual_support", "no": "material_recommendations"
            } } }, "visual_support": { "prompt": "Here are some visual aids to help
            you:\n- Video Guide: {video_link}\n- Step Diagrams: {diagram_link}\n\nLet
            me know if anything is unclear or if you need further help!" }, "material_recommendations":
            { "prompt": "To complete this repair, you’ll need:\n- **{material_1}**:
            [Buy here]({link_1})\n- **{material_2}**: [Buy here]({link_2})\n- **{material_3}**:
            [Buy here]({link_3})\n\nWould you like local material suggestions or budget-friendly
            alternatives?", "input": { "type": "multiple_choice", "choices": ["Local
            materials", "Alternatives"], "next_step": "motivation_and_support" } },
            "motivation_and_support": { "prompt": "You’re doing great! Repairs can
            feel challenging, but you’ve got this. 😊 If you need help during the process,
            upload a photo, and I’ll assist further!" }, "end": { "prompt": "Thank
            you for using DIY Repair Assistant! If you have more items to fix, I’m
            here to help. Happy repairing! 🛠️" }, "fallback_response": { "prompt":
            "I’m here to assist only with repair-related questions for objects and
            household items. Let me know if you have something to fix!" } }'
        selected: false
        title: LLM
        type: llm
        variables: []
        vision:
          enabled: false
      height: 98
      id: llm
      position:
        x: 400.47294141431075
        y: 282
      positionAbsolute:
        x: 400.47294141431075
        y: 282
      selected: true
      sourcePosition: right
      targetPosition: left
      type: custom
      width: 244
    - data:
        answer: '{{#llm.text#}}'
        desc: ''
        selected: false
        title: Answer
        type: answer
        variables: []
      height: 103
      id: answer
      position:
        x: 740.4923598739865
        y: 282
      positionAbsolute:
        x: 740.4923598739865
        y: 282
      selected: false
      sourcePosition: right
      targetPosition: left
      type: custom
      width: 244
    viewport:
      x: 24.23124094012269
      y: 87.10651889185854
      zoom: 0.790997959040624
```
