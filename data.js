{
  "kind": "app",
  "version": "0.1.5",
  "description": "Assisting you in the process of reparations of various different objects.",
  "icon": "🤖",
  "icon_background": "#FFEAD5",
  "mode": "advanced-chat",
  "name": "DIY - reparation assistent",
  "use_icon_as_answer_icon": true,
  "workflow": {
    "conversation_variables": [],
    "environment_variables": [],
    "features": {
      "file_upload": {
        "allowed_file_extensions": [".JPG", ".JPEG", ".PNG", ".GIF", ".WEBP", ".SVG"],
        "allowed_file_types": ["image"],
        "allowed_file_upload_methods": ["local_file", "remote_url"],
        "enabled": false,
        "fileUploadConfig": {
          "audio_file_size_limit": 50,
          "batch_count_limit": 5,
          "file_size_limit": 15,
          "image_file_size_limit": 10,
          "video_file_size_limit": 100,
          "workflow_file_upload_limit": 10
        },
        "image": {
          "enabled": false,
          "number_limits": 3,
          "transfer_methods": ["local_file", "remote_url"]
        },
        "number_limits": 3
      },
      "retriever_resource": {
        "enabled": true
      },
      "sensitive_word_avoidance": {
        "enabled": false
      },
      "speech_to_text": {
        "enabled": false
      },
      "suggested_requests": [
        "Help me fix a [specific item] that is [specific issue].",
        "What tools or materials do I need to repair a [specific item]?",
        "How do I replace a broken part in my [specific item]?",
        "Guide me through fixing a [specific item] with [visible damage].",
        "Can you help me diagnose why my [specific item] is not working?"
      ],
      "suggested_questions_after_answer": {
        "enabled": false
      },
      "text_to_speech": {
        "enabled": false,
        "language": "",
        "voice": ""
      },
      "opening_statement": "Hello! I'm your DIY Repair Assistant. 🛠️\n\nI’m here to help you repair household items with step-by-step guidance based on common repair techniques and examples. Please note that my suggestions are general and may need some adaptation to fit your specific situation. Also, I only assist with **item repairs**—not medical, legal, or other non-repair-related topics.\n\nTo get started, here’s how you can help me help you:\n1️⃣ Tell me what item you’re repairing (e.g., chair, faucet, phone).\n2️⃣ Describe the specific issue (e.g., wobbly, leaking, not turning on).\n3️⃣ Let me know if there’s any visible damage (e.g., cracks, wear, fraying).\n\nYou can also upload a photo of the item for more precise guidance. Let’s fix it together!"
    },
    "graph": {
      "edges": [
        {
          "data": {
            "sourceType": "start",
            "targetType": "llm"
          },
          "id": "start-to-llm",
          "source": "start",
          "target": "llm",
          "type": "custom"
        },
        {
          "data": {
            "sourceType": "llm",
            "targetType": "visual_support"
          },
          "id": "llm-to-visual-support",
          "source": "llm",
          "target": "visual_support",
          "type": "custom"
        },
        {
          "data": {
            "sourceType": "visual_support",
            "targetType": "material_recommendations"
          },
          "id": "visual-support-to-material-recommendations",
          "source": "visual_support",
          "target": "material_recommendations",
          "type": "custom"
        },
        {
          "data": {
            "sourceType": "material_recommendations",
            "targetType": "motivation_and_support"
          },
          "id": "material-recommendations-to-motivation",
          "source": "material_recommendations",
          "target": "motivation_and_support",
          "type": "custom"
        },
        {
          "data": {
            "sourceType": "motivation_and_support",
            "targetType": "check_another_repair"
          },
          "id": "motivation-to-check",
          "source": "motivation_and_support",
          "target": "check_another_repair",
          "type": "custom"
        },
        {
          "data": {
            "sourceType": "check_another_repair",
            "targetType": "start",
            "condition": "yes"
          },
          "id": "check-to-start",
          "source": "check_another_repair",
          "target": "start",
          "type": "custom"
        },
        {
          "data": {
            "sourceType": "check_another_repair",
            "targetType": "end",
            "condition": "no"
          },
          "id": "check-to-end",
          "source": "check_another_repair",
          "target": "end",
          "type": "custom"
        }
      ],
      "nodes": [
        {
          "data": {
            "title": "Start",
            "desc": "Initial node where the repair process begins.",
            "type": "start"
          },
          "id": "start",
          "position": {
            "x": 80,
            "y": 100
          }
        },
        {
          "data": {
            "title": "Visual Support",
            "desc": "Provides visual aids (diagrams, videos) to help with the repair.",
            "type": "visual_support",
            "prompt": "Here are some visual aids to help you:\n- **Video Guide**: {video_link}\n- **Step Diagrams**: {diagram_link}\n\nLet me know if you need further clarification!",
            "next_step": "material_recommendations"
          },
          "id": "visual_support",
          "position": {
            "x": 300,
            "y": 200
          }
        },
        {
          "data": {
            "title": "Material Recommendations",
            "desc": "Suggests materials and tools needed for the repair.",
            "type": "material_recommendations",
            "prompt": "To complete this repair, you’ll need:\n- **{material_1}**: [Buy here]({link_1})\n- **{material_2}**: [Buy here]({link_2})\n- **{material_3}**: [Buy here]({link_3})\n\nWould you like me to find materials in your local area or suggest alternatives?",
            "input": {
              "type": "multiple_choice",
              "choices": ["Local materials", "Alternatives"]
            },
            "next_step": "motivation_and_support"
          },
          "id": "material_recommendations",
          "position": {
            "x": 300,
            "y": 400
          }
        },
        {
          "data": {
            "title": "Motivation and Support",
            "desc": "Motivates the user and provides encouragement.",
            "type": "motivation_and_support",
            "prompt": "You’re doing great! Keep going—you’ll have this fixed in no time. 😊\n\nIf you run into any trouble, feel free to ask me questions or upload a picture of your progress."
          },
          "id": "motivation_and_support",
          "position": {
            "x": 500,
            "y": 600
          }
        },
        {
          "data": {
            "title": "Check Another Repair",
            "desc": "Asks if the user has more items to repair.",
            "type": "check_another_repair",
            "prompt": "Is there anything else I can help you with? For example, do you have another item that needs repair?",
            "input": {
              "type": "yes_no",
              "next_step": {
                "yes": "start",
                "no": "end"
              }
            }
          },
          "id": "check_another_repair",
          "position": {
            "x": 700,
            "y": 800
          }
        },
        {
          "data": {
            "title": "End",
            "desc": "Thank the user and end the interaction.",
            "type": "end",
            "prompt": "Thank you for using DIY Repair Assistant! If you have more items to fix in the future, I’m always here to help.
